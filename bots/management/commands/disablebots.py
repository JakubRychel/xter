from .base_bot_command import BaseBotCommand

class Command(BaseBotCommand):
    help = 'Enable multiple bots'
    enable = False
    single = False

    def add_arguments(self, parser):
        parser.add_argument(
            'usernames',
            nargs='*',
            type=str,
            help='Usernames of the bots to disable'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Disable all bots'
        )