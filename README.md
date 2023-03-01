# Academic Article Renamer

Academic Article Renamer (artitle) is a command-line interface (CLI) tool that renames academic articles to their titles. It solves the problem of cryptic default file names that many academic article repositories provide. The CLI uses the [Grobid](https://grobid.readthedocs.io/en/latest/) server to extract the title from the PDF file and renames the file accordingly.

## Installation

You can install artitle using pip:

```sh
pip install artitle
```

# Usage

To use artitle, you must have the Grobid server running on your computer. You can refer to the Grobid documentation for information on how to run the server.

According to our observations Grobid needs to eat up substantial amounts of memory to be able to perform it's job. We recommend to allocate at least `6GB` memory for Grobid Server to avoid runtime failures. To run the container with `6GB` memory you could type following command:

```bash
docker run -m 6g -p 8070:8070 grobid/grobid:0.7.2
```

Once you have the Grobid server running, you can use the CLI to rename your article PDFs. To rename all the PDFs in a directory, run the following command:

```shell
artitle <path-to-pdf-files>
```

he <path-to-pdf-files> argument should be the path to the directory containing the PDF files that you want to rename.

By default, the CLI uses underscores (_) to replace spaces in the file names. If you want to use a different character to replace spaces, you can specify it using the -s or --space-replace option:

```shell
artitle <path-to-pdf-files> -s "-"
```

This command uses hyphens (-) to replace spaces in the file names.

The program creates a new directory named pdfs_with_old_names inside the directory containing the PDF files. Before renaming any PDF files, the program copies the original PDF files into this directory with their original names, so that you can easily revert the changes if anything goes wrong.

After renaming the PDF files, the program creates a file named renaming.txt inside the directory containing the PDF files. This file contains information about the renaming of each PDF file, with one row for each file. The rows include the original file name, the new file name, and any characters that were replaced with hyphens (-) because they could cause problems in file names.

Grobid Server generates an XML file for each processed PDF file. These XML files are stored in xml directory inside the directory containing PDF files.

# License

Academic Article Renamer is licensed under the MIT License. See the LICENSE file for more information.
