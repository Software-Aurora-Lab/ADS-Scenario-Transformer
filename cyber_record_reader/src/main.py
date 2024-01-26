import argparse

from CyberRecordReader import CyberRecordReader


def main():
    """
    - Usage: poetry run python3 src/main.py --filepath=./apollo_borregas/00000009.00000 
    - Usage: poetry run python3 src/main.py --filepath=./apollo_borregas/00000009.00000 --channel="/apollo/routing_response_history"
    
    """
    parser = argparse.ArgumentParser(
        description=
        'Generate cyber_record command based on input filename and target channel'
    )
    parser.add_argument('--filepath', help='Input file path')
    parser.add_argument('--channel', help='Input file path', default="all")

    args = parser.parse_args()
    reader = CyberRecordReader()
    if args.channel == "all":
        reader.read_all_channels(source_path=args.filepath)
    else:

        if not args.channel:
            print("Missing channel name")
            return

        target_channel = next(
            member for name, member in
            CyberRecordReader.TargetChannels.__members__.items()
            if member.value == args.channel)

        if target_channel:
            reader.read_channel(source_path=args.filepath,
                                channel=target_channel)
        else:
            print(f"Invalid channel: {args.channel}")


if __name__ == "__main__":
    main()
