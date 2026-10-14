export interface Board {
  id: string;
  title: string;
}

export async function connect(url: string) {
  if (!url) throw new Error("DATABASE_URL is not set");
  const boards: Board[] = [];
  return {
    listBoards: async (): Promise<Board[]> => boards,
  };
}
