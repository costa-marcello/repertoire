-- Language servers are installed by Mason, not by hand.
-- After pulling changes, run :Lazy sync, then :MasonInstall for any new server.
return {
  { "williamboman/mason.nvim", config = true },
  {
    "neovim/nvim-lspconfig",
    dependencies = { "williamboman/mason.nvim" },
    config = function()
      require("lspconfig").lua_ls.setup({})
      require("lspconfig").pyright.setup({})
    end,
  },
}
