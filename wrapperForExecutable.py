from cdrfgzip import cdrfgzip
from csvftar import csvftar

import argparse


def run_compressCdr():
  print("Please provide the required information for compressing CDR files:")
  path = input("Enter the folder path to CDR files (required): ")
  if not path:
    print("Error: The path to CDR files is required.")
    return

  # Optional arguments can be skipped by pressing Enter
  output = input("Enter the output zip file path (leave blank to use PATH): ")
  maxlines = input("Enter the max CDR number in one csv file (leave blank for default): ")
  filter = input("Enter the filter file (phone.csv) path (leave blank if not used): ")
  compress = input("Specify the compressed format (gzip) if original CDR files are gzip (leave blank if they are plain csv): ")

  args = argparse.Namespace(
      path=path,
      output=output if output else None,  # Use None if no input was provided
      maxlines=maxlines if maxlines else None,
      filter=filter if filter else None,
      compress=compress if compress else None
  )

  cdrfgzip.main(args);

def run_compressCsv():
  print("Please provide the required information for compressing CSV files:")
  input_path = input("Enter the input tarfile path (required): ")
  if not input_path:
    print("Error: The input tarfile path is required.")
    return

  # Optional arguments can be skipped by pressing Enter
  filter_path = input("Enter the filter csv file path (leave blank if not used): ")
  output_dir = input("Enter the output directory path (leave blank to use the dir of input tarfile path): ")

  args = argparse.Namespace(
      input=input_path,
      filter=filter_path if filter_path else None,  # Use None if no input was provided
      output=output_dir if output_dir else None
  )

  csvftar.main(args)

def show_help():
  print("Available commands:")
  print("compressCdr - It runs compressCdr script. This compress available CDR's to single gzip file.")
  print("compressCsv - It runs compressCsv script. This removes unwanted columns from phone and enduser csv's. ")
  print("help - Show help messagse")
  print("exit - Exit the launcher")

def main():
  while True:
    user_input = input("Enter a command (compress_cdr, compress_csv, help, exit): ").strip().lower()
    if user_input == 'compress_cdr':
      run_compressCdr()
    elif user_input == 'compress_csv':
      run_compressCsv()
    elif user_input == 'help':
      show_help()
    elif user_input == 'exit':
      break
    else:
      print("Unknown command. Type 'help' for a list of commands.")

if __name__ == "__main__":
  main()
