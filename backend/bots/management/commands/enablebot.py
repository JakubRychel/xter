from .base_bot_command import BaseBotCommand

class Command(BaseBotCommand):
    help = 'Enable a single bot'
    enable = True
    single = True

    def add_arguments(self, parser):
        parser.add_argument(
            'username',
            type=str,
            help='Username of the bot to enable'
        )