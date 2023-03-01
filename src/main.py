import argparse
import json
import tempfile
import os
import shutil
import xml.etree.ElementTree as ET
from .grobid_client import GrobidClient


def get_title_text(xml_file_path):
    # Parse the XML file
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Define the namespace dictionary
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

    # Find the title element inside the titleStmt element
    title_stmt = root.find('.//tei:titleStmt', ns)
    title = title_stmt.find('tei:title', ns)

    # Get the text inside the title element
    title_text = title.text

    # Return the text
    return title_text

def rename_pdfs_with_titles(pdf_dir, xml_dir, whitespace_char='_'):
    # Create the pdfs_with_old_names directory
    os.makedirs(os.path.join(pdf_dir, 'pdfs_with_old_names'), exist_ok=True)

    # Create the renaming.txt file
    with open(os.path.join(pdf_dir, 'renaming.txt'), 'w') as f:
        f.write('Old name -> New name\n')

    # Initialize counters
    renamed_count = 0
    skipped_count = 0
    skipped_files = []

    # Loop over the pdf files in the pdf_dir directory
    for pdf_file in os.listdir(pdf_dir):
        if pdf_file.endswith('.pdf'):
            # Get the corresponding xml file path
            xml_file = os.path.join(xml_dir, os.path.splitext(pdf_file)[0] + '.tei.xml')

            # Skip if the xml file doesn't exist
            if not os.path.exists(xml_file):
                print(f"Skipping {pdf_file} - corresponding xml file not found")
                skipped_count += 1
                skipped_files.append(pdf_file)
                continue

            # Get the title text from the xml file
            title = get_title_text(xml_file)

            # Replace whitespace characters with the specified character
            title = whitespace_char.join(title.split())

            # Replace problematic characters with -
            title_safe = title.translate(str.maketrans({
                '/': '-',
                '\\': '-',
                ':': '-',
                '*': '-',
                '?': '-',
                '"': '-',
                '<': '-',
                '>': '-',
                '|': '-'
            }))

            # Check if the title contains problematic characters
            if title != title_safe:
                print(f"Title '{title}' contains problematic characters - replacing with '{title_safe}'")

            # Limit the title to 240 characters
            title_safe = title_safe[:240]

            # Copy the pdf file to pdfs_with_old_names directory
            pdf_path = os.path.join(pdf_dir, pdf_file)
            old_pdf_path = os.path.join(pdf_dir, 'pdfs_with_old_names', pdf_file)
            shutil.copy(pdf_path, old_pdf_path)

            # Rename the pdf file to {title}.pdf
            new_pdf_path = os.path.join(pdf_dir, title_safe + '.pdf')
            os.rename(pdf_path, new_pdf_path)

            # Append to the renaming.txt file
            with open(os.path.join(pdf_dir, 'renaming.txt'), 'a') as f:
                f.write(f"{pdf_file} -> {title_safe}.pdf\n")

            # Print informative message to console
            print(f"Renamed {pdf_file} to {title_safe}.pdf")
            renamed_count += 1

    print("Renaming process complete.")
    print(f"{renamed_count} PDFs renamed successfully.")
    print(f"{skipped_count} PDFs couldn't be renamed:")
    for file in skipped_files:
        print(f"- {file}")


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Rename article PDFs with their title')
    parser.add_argument('pdf_dir', help='path to directory containing PDF files')
    parser.add_argument('--whitespace-char', '-w', default='_',
                        help='character to use for whitespace in file names (default: _)')
    parser.add_argument('--grobid-port', '-p', type=int, default=8070,
                        help='port number of the Grobid server (default: 8070)')
    parser.add_argument("-d", "--delete", action="store_true", help="delete xml, pdfs_with_old_names directories, and renaming.txt")
    args = parser.parse_args()

    if args.delete:
        shutil.rmtree(os.path.join(args.pdf_dir, 'pdfs_with_old_names'))
        shutil.rmtree(os.path.join(args.pdf_dir, 'xml'))
        os.remove(os.path.join(args.pdf_dir, 'renaming.txt'))
        exit()

    # Check if pdf_dir exists
    if not os.path.exists(args.pdf_dir):
        print(f"Error: directory '{args.pdf_dir}' does not exist.")
        exit()

    # Create the xml directory
    xml_dir = os.path.join(args.pdf_dir, 'xml')
    os.makedirs(xml_dir, exist_ok=True)

    # Modify the Grobid configuration
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')) as f:
        config = json.load(f)
    config['grobid_server'] = f"http://localhost:{args.grobid_port}"
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        json.dump(config, tmp, indent=4)
        tmp.flush()

    # Grobid processing
    client = GrobidClient(config_path=tmp.name)
    client.process("processFulltextDocument", args.pdf_dir, xml_dir, n=1)
    rename_pdfs_with_titles(args.pdf_dir, xml_dir)


if __name__ == '__main__':
    main()
