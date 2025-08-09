from django.core.management.base import BaseCommand
import os
import schedule
import time
import joblib
from django.conf import settings
from collections import defaultdict
from sklearn.linear_model import SGDRegressor
from ...models import InteractionEmbedding, UserRecommendationModel, GlobalRecommendationModel

def save_model(X, y, user_id, name):
    if user_id is not None:
        model_path = f'models_storage/users/{user_id}.pkl'
    elif name is not None:
        model_path = f'models_storage/global/{name}.pkl'
    else:
        raise ValueError('Must provide either user_id or name for model saving.')

    full_model_path = os.path.join(settings.MEDIA_ROOT, model_path)

    try:
        model = joblib.load(full_model_path)
        model.partial_fit(X, y)
    except (FileNotFoundError, EOFError, Exception):
        model = SGDRegressor()
        model.fit(X, y)

    os.makedirs(os.path.dirname(full_model_path), exist_ok=True)
    joblib.dump(model, full_model_path)
    
    if user_id is not None:
        model_obj, created = UserRecommendationModel.objects.get_or_create(user_id=user_id)
    elif name is not None:
        model_obj, created = GlobalRecommendationModel.objects.get_or_create(name=name)

    model_obj.model.name = model_path
    model_obj.save()

def train_models():
    embeddings = list(InteractionEmbedding.objects.filter(used_in_model=False))

    if not embeddings:
        return

    X_global = [list(e.embedding) for e in embeddings]
    y_global = [e.label for e in embeddings]

    save_model(X_global, y_global, name='default')
    
    embeddings_by_user = defaultdict(list)

    for e in embeddings:
        embeddings_by_user[e.user_id].append(e)

    for user_id, interactions in embeddings_by_user.items():
        X = [list(i.embedding) for i in interactions]
        y = [i.label for i in interactions]

        save_model(X, y, user_id=user_id)

        for i in interactions:
            i.used_in_model = True

    InteractionEmbedding.objects.bulk_update(embeddings, ['used_in_model'])

class Command(BaseCommand):
    help = 'Run recommendations training'

    def handle(self, *args, **kwargs):
        schedule.every().hour.at(':00').do(train_models)
        self.stdout.write(self.style.SUCCESS('Recommendations training started...'))

        try:
            while True:
                schedule.run_pending()
                self.stdout.write(self.style.SUCCESS('Action taken'))
                time.sleep(60)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Recommendations training stopped by user (Ctrl+C)'))