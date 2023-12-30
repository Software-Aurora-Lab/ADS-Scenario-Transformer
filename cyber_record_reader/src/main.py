import argparse

from CyberRecordReader import CyberRecordReader


def main():
    parser = argparse.ArgumentParser(
        description=
        'Generate cyber_record command based on input filename and target channel'
    )
    parser.add_argument('filepath', help='Input file path')

    args = parser.parse_args()
    reader = CyberRecordReader()
    reader.read_all_channels(file_path=args.filepath)

if __name__ == "__main__":
    main()