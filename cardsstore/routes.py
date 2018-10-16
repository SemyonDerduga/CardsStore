from .views import frontend


def setup_routes(app):
    router = app.router
    router.add_get('/', frontend.index, name='index')
    router.add_post('/login', frontend.login, name='login')
    router.add_get('/search', frontend.search_page, name='search')
    router.add_get('/card', frontend.card_view_page, name='card')
    router.add_get('/logout', frontend.logout, name='logout')
