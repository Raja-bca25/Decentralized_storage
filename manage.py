import os
import sys
import logging
from dotenv import load_dotenv
from django.core.management import execute_from_command_line
def main():
    load_dotenv
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.getenv('DJANGO_SETTINGS_MODULE', 'Secure_storage.settings'))
    logging.basicConfig(level=logging.ERROR)
    try:
        execute_from_command_line(sys.argv)
    except Exception as exc:
        logging.error("Error while executing Django command line:", exc_info=exc)
        sys.exit(1)
if __name__ == "__main__":
    main()