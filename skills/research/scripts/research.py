#!/usr/bin/env python3
"""
research - Research a topic on Reddit + X.

Usage:
    python research.py <topic> [options]
    (use python3 where the python command is missing)

Requires Python 3.9 or later; standard library only.

Network: api.openai.com (Reddit discovery, model list), api.x.ai (X search),
www.reddit.com (public thread JSON for engagement metrics). Only the sources
whose API key is set are called; with no keys the script makes no requests.

Options:
    --mock              Use fixtures instead of real API calls
    --emit=MODE         Output mode: compact|json|md|context|path (default: compact)
    --sources=MODE      Source selection: auto|reddit|x|both (default: auto)
    --quick             Faster research with fewer sources (15-25 Reddit, 8-12 X)
    --deep              Comprehensive research with more sources (70-100 Reddit, 40-60 X)
    --debug             Enable verbose debug logging
    --include-web       Also ask for web coverage: print the WEBSEARCH REQUIRED
                        block alongside the Reddit/X results

Time: the run stays under 10 minutes, so a 600000 ms shell timeout covers it.
Each Responses API search is tried once (90-180 s timeout by depth), and
Reddit enrichment stops at ENRICH_DEADLINE_SECONDS after the start.
"""

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

# Add lib to path. The script finds its own files from its own location,
# so it works from a plugin cache, a junction, or any install folder.
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

# Captured output on Windows defaults to a legacy code page that cannot
# encode the emoji and box characters below; force UTF-8 instead.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

from lib import (
    dates,
    dedupe,
    env,
    http,
    models,
    normalize,
    openai_reddit,
    reddit_enrich,
    render,
    schema,
    score,
    ui,
    websearch,
    xai_x,
)


# Seconds after the start at which Reddit enrichment stops, so the run ends
# inside the skill's 600000 ms shell timeout. The model list (about 1.5
# minutes at worst) and a Reddit search plus its retry (3 minutes each at
# --deep) end by about 7.5 minutes; an enrichment request still in flight at
# the deadline adds at most about 1.5 minutes, so the worst case is 8.5.
ENRICH_DEADLINE_SECONDS = 420


def load_fixture(name: str) -> dict:
    """Load a fixture file."""
    fixture_path = SCRIPT_DIR / "fixtures" / name
    if fixture_path.exists():
        with open(fixture_path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _search_reddit(
    topic: str,
    config: dict,
    selected_models: dict,
    from_date: str,
    to_date: str,
    depth: str,
    mock: bool,
) -> tuple:
    """Search Reddit via OpenAI (runs in thread).

    Returns:
        Tuple of (reddit_items, raw_openai, error)
    """
    raw_openai = None
    reddit_error = None

    if mock:
        raw_openai = load_fixture("openai_sample.json")
    else:
        try:
            raw_openai = openai_reddit.search_reddit(
                config["OPENAI_API_KEY"],
                selected_models["openai"],
                topic,
                from_date,
                to_date,
                depth=depth,
            )
        except http.HTTPError as e:
            raw_openai = {"error": str(e)}
            reddit_error = f"API error: {e}"
        except Exception as e:
            raw_openai = {"error": str(e)}
            reddit_error = f"{type(e).__name__}: {e}"

    # Parse response. A reply with no readable items list is an error, so
    # reddit.com is not reported as covered and the subagents search it.
    reddit_items = []
    if not reddit_error:
        try:
            reddit_items = openai_reddit.parse_reddit_response(raw_openai or {})
        except http.BadResponseError as e:
            reddit_error = f"Bad response: {e}"

    # Quick retry with simpler query if few results
    if len(reddit_items) < 5 and not mock and not reddit_error:
        core = openai_reddit._extract_core_subject(topic)
        if core.lower() != topic.lower():
            try:
                retry_raw = openai_reddit.search_reddit(
                    config["OPENAI_API_KEY"],
                    selected_models["openai"],
                    core,
                    from_date, to_date,
                    depth=depth,
                )
                retry_items = openai_reddit.parse_reddit_response(retry_raw)
                # Add items not already found (by URL)
                existing_urls = {item.get("url") for item in reddit_items}
                for item in retry_items:
                    if item.get("url") not in existing_urls:
                        reddit_items.append(item)
            except (http.HTTPError, KeyError, TypeError, ValueError, json.JSONDecodeError) as e:
                http.log(f"Retry query failed: {e}")

    return reddit_items, raw_openai, reddit_error


def _search_x(
    topic: str,
    config: dict,
    selected_models: dict,
    from_date: str,
    to_date: str,
    depth: str,
    mock: bool,
) -> tuple:
    """Search X via xAI (runs in thread).

    Returns:
        Tuple of (x_items, raw_xai, error)
    """
    raw_xai = None
    x_error = None

    if mock:
        raw_xai = load_fixture("xai_sample.json")
    else:
        try:
            raw_xai = xai_x.search_x(
                config["XAI_API_KEY"],
                selected_models["xai"],
                topic,
                from_date,
                to_date,
                depth=depth,
            )
        except http.HTTPError as e:
            raw_xai = {"error": str(e)}
            x_error = f"API error: {e}"
        except Exception as e:
            raw_xai = {"error": str(e)}
            x_error = f"{type(e).__name__}: {e}"

    # Parse response. A reply with no readable items list is an error, so
    # x.com is not reported as covered.
    x_items = []
    if not x_error:
        try:
            x_items = xai_x.parse_x_response(raw_xai or {})
        except http.BadResponseError as e:
            x_error = f"Bad response: {e}"

    return x_items, raw_xai, x_error


def run_research(
    topic: str,
    sources: str,
    config: dict,
    selected_models: dict,
    from_date: str,
    to_date: str,
    depth: str = "default",
    mock: bool = False,
    progress: ui.ProgressDisplay = None,
    deadline: float = None,
) -> tuple:
    """Run the research pipeline.

    deadline is a time.monotonic() value; Reddit enrichment stops once it
    passes, and the threads not yet enriched keep no engagement metrics.

    Returns:
        Tuple of (reddit_items, x_items, web_needed, raw_openai, raw_xai, raw_reddit_enriched, reddit_error, x_error)

    Note: web_needed is True in web-only mode and with --include-web. The
    script then prints the WEBSEARCH REQUIRED block (see output_result); in
    the research skill, the Phase 2 subagents provide that web coverage.
    """
    reddit_items = []
    x_items = []
    raw_openai = None
    raw_xai = None
    raw_reddit_enriched = []
    reddit_error = None
    x_error = None

    # Check if web coverage is needed (always needed in web-only mode)
    web_needed = sources in ("all", "web", "reddit-web", "x-web")

    # Web-only mode: no API calls needed, Claude handles everything
    if sources == "web":
        if progress:
            progress.start_web_only()
            progress.end_web_only()
        return reddit_items, x_items, True, raw_openai, raw_xai, raw_reddit_enriched, reddit_error, x_error

    # Determine which searches to run
    run_reddit = sources in ("both", "reddit", "all", "reddit-web")
    run_x = sources in ("both", "x", "all", "x-web")

    # Run Reddit and X searches in parallel
    reddit_future = None
    x_future = None

    with ThreadPoolExecutor(max_workers=2) as executor:
        # Submit both searches
        if run_reddit:
            if progress:
                progress.start_reddit()
            reddit_future = executor.submit(
                _search_reddit, topic, config, selected_models,
                from_date, to_date, depth, mock
            )

        if run_x:
            if progress:
                progress.start_x()
            x_future = executor.submit(
                _search_x, topic, config, selected_models,
                from_date, to_date, depth, mock
            )

        # Collect results
        if reddit_future:
            try:
                reddit_items, raw_openai, reddit_error = reddit_future.result()
                if reddit_error and progress:
                    progress.show_error(f"Reddit error: {reddit_error}")
            except Exception as e:
                reddit_error = f"{type(e).__name__}: {e}"
                if progress:
                    progress.show_error(f"Reddit error: {e}")
            if progress:
                progress.end_reddit(len(reddit_items))

        if x_future:
            try:
                x_items, raw_xai, x_error = x_future.result()
                if x_error and progress:
                    progress.show_error(f"X error: {x_error}")
            except Exception as e:
                x_error = f"{type(e).__name__}: {e}"
                if progress:
                    progress.show_error(f"X error: {e}")
            if progress:
                progress.end_x(len(x_items))

    # Enrich Reddit items with real data (sequential, but with error handling per-item)
    if reddit_items:
        if progress:
            progress.start_reddit_enrich(1, len(reddit_items))

        skipped = 0
        for i, item in enumerate(reddit_items):
            if deadline is not None and time.monotonic() > deadline:
                skipped = len(reddit_items) - i
                break
            if progress and i > 0:
                progress.update_reddit_enrich(i + 1, len(reddit_items))

            try:
                if mock:
                    mock_thread = load_fixture("reddit_thread_sample.json")
                    reddit_items[i] = reddit_enrich.enrich_reddit_item(item, mock_thread)
                else:
                    reddit_items[i] = reddit_enrich.enrich_reddit_item(item)
            except Exception as e:
                # Log but don't crash - keep the unenriched item
                if progress:
                    progress.show_error(f"Enrich failed for {item.get('url', 'unknown')}: {e}")

            raw_reddit_enriched.append(reddit_items[i])

        if progress:
            progress.end_reddit_enrich()

        # Say why metrics are missing instead of leaving it silent
        if skipped and progress:
            progress.show_error(
                f"Time limit reached: {skipped} of {len(reddit_items)} Reddit threads "
                "were not enriched and have no engagement metrics"
            )
        tried = reddit_items[:len(reddit_items) - skipped]
        missing = sum(1 for item in tried if not item.get("engagement"))
        if missing and progress:
            progress.show_error(
                f"No engagement metrics for {missing} of {len(tried)} Reddit threads: "
                "reddit.com did not return the thread data (rerun with --debug for details)"
            )

    return reddit_items, x_items, web_needed, raw_openai, raw_xai, raw_reddit_enriched, reddit_error, x_error


def main():
    parser = argparse.ArgumentParser(
        description="Research a topic on Reddit + X"
    )
    parser.add_argument("topic", nargs="?", help="Topic to research")
    parser.add_argument("--mock", action="store_true", help="Use fixtures")
    parser.add_argument(
        "--emit",
        choices=["compact", "json", "md", "context", "path"],
        default="compact",
        help="Output mode",
    )
    parser.add_argument(
        "--sources",
        choices=["auto", "reddit", "x", "both"],
        default="auto",
        help="Source selection",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Faster research with fewer sources (15-25 Reddit, 8-12 X)",
    )
    parser.add_argument(
        "--deep",
        action="store_true",
        help="Comprehensive research with more sources (70-100 Reddit, 40-60 X)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable verbose debug logging",
    )
    parser.add_argument(
        "--include-web",
        action="store_true",
        help="Also print the WEBSEARCH REQUIRED block, asking for web coverage alongside Reddit/X",
    )

    args = parser.parse_args()
    deadline = time.monotonic() + ENRICH_DEADLINE_SECONDS

    # Enable debug logging if requested
    if args.debug:
        os.environ["RESEARCH_DEBUG"] = "1"
        # Re-import http to pick up debug flag
        from lib import http as http_module
        http_module.DEBUG = True

    # Determine depth
    if args.quick and args.deep:
        print("Error: Cannot use both --quick and --deep", file=sys.stderr)
        sys.exit(1)
    elif args.quick:
        depth = "quick"
    elif args.deep:
        depth = "deep"
    else:
        depth = "default"

    if not args.topic:
        print("Error: Please provide a topic to research.", file=sys.stderr)
        print("Usage: python research.py <topic> [options]", file=sys.stderr)
        sys.exit(1)

    # Load config
    config = env.get_config()

    # Check available sources
    available = env.get_available_sources(config)

    # Mock mode can work without keys
    if args.mock:
        if args.sources == "auto":
            sources = "both"
        else:
            sources = args.sources
    else:
        # Validate requested sources against available
        sources, error = env.validate_sources(args.sources, available, args.include_web)
        if error:
            # The web-only note is a warning: print it and continue
            if error.startswith(env.WEB_ONLY_NOTE):
                print(f"Note: {error}", file=sys.stderr)
            else:
                print(f"Error: {error}", file=sys.stderr)
                sys.exit(1)

    # Get date range (the lookback window stated in SKILL.md)
    from_date, to_date = dates.get_date_range(dates.LOOKBACK_DAYS)

    # Check what keys are missing for promo messaging
    missing_keys = env.get_missing_keys(config)

    # Initialize progress display
    progress = ui.ProgressDisplay(args.topic, show_banner=True)

    # Select models
    if args.mock:
        # Use mock models
        mock_openai_models = load_fixture("models_openai_sample.json").get("data", [])
        mock_xai_models = load_fixture("models_xai_sample.json").get("data", [])
        selected_models = models.get_models(
            {
                **config,
                "OPENAI_API_KEY": "mock",
                "XAI_API_KEY": "mock",
            },
            mock_openai_models,
            mock_xai_models,
        )
    else:
        selected_models = models.get_models(config)

    # Determine mode string
    if sources == "all":
        mode = "all"  # reddit + x + web
    elif sources == "both":
        mode = "both"  # reddit + x
    elif sources == "reddit":
        mode = "reddit-only"
    elif sources == "reddit-web":
        mode = "reddit-web"
    elif sources == "x":
        mode = "x-only"
    elif sources == "x-web":
        mode = "x-web"
    elif sources == "web":
        mode = "web-only"
    else:
        mode = sources

    # Run research
    reddit_items, x_items, web_needed, raw_openai, raw_xai, raw_reddit_enriched, reddit_error, x_error = run_research(
        args.topic,
        sources,
        config,
        selected_models,
        from_date,
        to_date,
        depth,
        args.mock,
        progress,
        deadline,
    )

    # Processing phase
    progress.start_processing()

    # Normalize items
    normalized_reddit = normalize.normalize_reddit_items(reddit_items, from_date, to_date)
    normalized_x = normalize.normalize_x_items(x_items, from_date, to_date)

    # Hard date filter: exclude items with verified dates outside the range
    # This is the safety net - even if prompts let old content through, this filters it
    filtered_reddit = normalize.filter_by_date_range(normalized_reddit, from_date, to_date)
    filtered_x = normalize.filter_by_date_range(normalized_x, from_date, to_date)

    # Score items
    scored_reddit = score.score_reddit_items(filtered_reddit)
    scored_x = score.score_x_items(filtered_x)

    # Sort items
    sorted_reddit = score.sort_items(scored_reddit)
    sorted_x = score.sort_items(scored_x)

    # Dedupe items
    deduped_reddit = dedupe.dedupe_reddit(sorted_reddit)
    deduped_x = dedupe.dedupe_x(sorted_x)

    progress.end_processing()

    # Create report
    report = schema.create_report(
        args.topic,
        from_date,
        to_date,
        mode,
        selected_models.get("openai"),
        selected_models.get("xai"),
    )
    report.reddit = deduped_reddit
    report.x = deduped_x
    report.reddit_error = reddit_error
    report.x_error = x_error

    # Generate context snippet
    report.context_snippet_md = render.render_context_snippet(report)

    # Write outputs. The report still goes to stdout if the folder can't be written.
    try:
        render.write_outputs(report, raw_openai, raw_xai, raw_reddit_enriched)
    except OSError as e:
        progress.show_error(f"Could not write the report files to {render.OUTPUT_DIR}: {e}")

    # Show completion
    if sources == "web":
        progress.show_web_only_complete()
    else:
        progress.show_complete(len(deduped_reddit), len(deduped_x))

    # Output result
    output_result(report, args.emit, web_needed, args.topic, from_date, to_date, missing_keys)


def output_result(
    report: schema.Report,
    emit_mode: str,
    web_needed: bool = False,
    topic: str = "",
    from_date: str = "",
    to_date: str = "",
    missing_keys: str = "none",
):
    """Output the result based on emit mode."""
    if emit_mode == "compact":
        print(render.render_compact(report, missing_keys=missing_keys))
    elif emit_mode == "json":
        print(json.dumps(report.to_dict(), indent=2))
    elif emit_mode == "md":
        print(render.render_full_report(report))
    elif emit_mode == "context":
        print(report.context_snippet_md)
    elif emit_mode == "path":
        print(render.get_context_path())

    # Web coverage notice. The research skill's SKILL.md ("Phase 1") reads
    # this block; keep the two in step.
    if web_needed:
        print("\n" + render.web_search_block(report, topic, from_date, to_date))


if __name__ == "__main__":
    main()
