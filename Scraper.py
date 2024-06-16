import aiohttp
import asyncio
import os
from rich.console import Console
from rich.progress import Progress

console = Console()

async def fetch_members(session, group, cursor):
    group_url = f"https://groups.roblox.com/v1/groups/{group}/users?sortOrder=Asc&limit=100&cursor={cursor}"
    try:
        async with session.get(group_url) as response:
            response.raise_for_status()  # Raises an error for bad status codes
            return await response.json()
    except aiohttp.ClientError as e:
        console.print(f"[bold red]An error occurred: {e}[/bold red]")
        return None

async def retrieve_members(group, cursor, id_list, progress):
    async with aiohttp.ClientSession() as session:
        next_cursor = cursor
        while next_cursor is not None:
            members = await fetch_members(session, group, next_cursor)
            if not members:
                break

            user_ids = [str(member['user']['userId']) for member in members.get('data', [])]
            console.print(f"Fetched [bold green]{len(user_ids)}[/bold green] members")
            if user_ids:
                id_list.write("\n".join(user_ids) + "\n")

            next_cursor = members.get('nextPageCursor')
            if next_cursor:
                console.print(f"Moving to next page with cursor: [bold blue]{next_cursor}[/bold blue]")

            # Adding a small delay to avoid hitting rate limits
            await asyncio.sleep(0.1)
            progress.update(task, advance=len(user_ids))

async def main():
    group_id = input("Enter the Group ID: ")

    try:
        file_path = os.path.join(os.path.dirname(__file__), 'userids.txt')
        with open(file_path, "a") as id_list:
            with Progress() as progress:
                global task
                task = progress.add_task("Fetching members...", start=False)
                await retrieve_members(group_id, "", id_list, progress)
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")

if __name__ == "__main__":
    console.print("[bold blue]Starting the Roblox Group User Id Scraper...[/bold blue]")
    asyncio.run(main())
    console.print("[bold green]Scraping complete! User IDs have been saved to userids.txt[/bold green]")
