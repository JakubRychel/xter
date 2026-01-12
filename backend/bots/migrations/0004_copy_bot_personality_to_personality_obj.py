from django.db import migrations


def copy_personalities(apps, schema_editor):
    Bot = apps.get_model('bots', 'Bot')
    Personality = apps.get_model('bots', 'Personality')

    for bot in Bot.objects.all():
        if bot.personality:
            p = Personality.objects.create(description=bot.personality)
            bot.personality_obj_id = p.id
            bot.save(update_fields=['personality_obj'])


class Migration(migrations.Migration):

    dependencies = [
        ('bots', '0003_personality_bot_personality_obj'),
    ]

    operations = [
        migrations.RunPython(copy_personalities, migrations.RunPython.noop),
    ]