import argparse
from db import add_book, remove_book, get_all_books

def main():
    parser = argparse.ArgumentParser(description="Kindle Book Price Tracker")
    subparsers = parser.add_subparsers(dest="command", help="Available commands", required=True)

    # Add book
    parser_add = subparsers.add_parser("add", help="Add a book using its Amazon URL")
    parser_add.add_argument("url", type=str, help="Amazon book URL")
    parser_add.add_argument("--title", type=str, help="Optional book title")
    parser_add.add_argument("--asin", type=str, help="Optional ASIN")

    # Remove book
    parser_remove = subparsers.add_parser('remove', help="Remove a book by ID")
    parser_remove.add_argument("id", type=int, help="Book ID to remove")

    #List books
    subparsers.add_parser("list", help="List all tracked books")

    args = parser.parse_args()


    if args.command == "add":
        add_book(args.url, title=args.title, asin=args.asin)
        #print("Book added successfully ✅")

    elif args.command == "remove":
        remove_book(args.id)
        print("Book removed successfully 🗑️")

    elif args.command == "list":
        books = get_all_books()
        print(
            f"DEBUG: Command = {args.command}, URL = {getattr(args, 'url', None)}, ASIN = {getattr(args, 'asin', None)}")
        if not books:
            print("No books are currently being tracked.")
        else:
            print("\n Tracked Books 📚:")
            for b in books:
                # I removed this {b[0]}]
                print(f" Title: {b[1] or '-'} | ASIN: {b[2] or '-'}\n URL: {b[3]}\n Last Prince: £{b[4] if b[4] is not None else '-'} | Last Check: {b[5] or '-'}\n")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()