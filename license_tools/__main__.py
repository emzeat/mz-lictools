
import license_tools
import sys

if __name__ == "__main__":
    try:
        license_tools.main()
    except Exception as e:
        print(e)
        sys.exit(1)
