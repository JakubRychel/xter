from django.core.management.base import BaseCommand
from ...models import Bot
from ...tasks import plan_next_task

class BaseBotCommand(BaseCommand):
    enable = True
    single = True

    def handle(self, *args, **options):
        all_flag = options.get('all', False)

        if self.single:
            username = options['username']
            usernames = [username]
        else:
            usernames = options['usernames']

        if all_flag:
            queryset = Bot.objects.all()
        else:
            queryset = Bot.objects.filter(user__username__in=usernames)

        if not queryset.exists():
            self.stdout.write(self.style.ERROR('No bots found'))
            return
        
        updated_count = queryset.update(enabled=self.enable)

        if self.enable:
            for bot in queryset:
                plan_next_task(bot.id)

        self.stdout.write(self.style.SUCCESS(
            f'{updated_count} {'bots' if updated_count > 1 else 'bot'} {'enabled' if self.enable else 'disabled'}'
        ))