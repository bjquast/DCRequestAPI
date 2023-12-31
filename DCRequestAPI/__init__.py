from pyramid.config import Configurator
from pyramid.renderers import JSONP

from pyramid.authentication import SessionAuthenticationPolicy
from pyramid_beaker import session_factory_from_settings

from dwb_authentication.security import SecurityPolicy


def main(global_config, **settings):
	config = Configurator(settings=settings)
	
	config.include('pyramid_beaker')
	session_factory = session_factory_from_settings(settings)
	config.set_security_policy(SecurityPolicy())
	
	config.include('pyramid_chameleon')
	config.add_renderer('jsonp', JSONP(param_name='callback'))
	
	config.add_route('iupartslist', '/list')
	config.add_route('help', '/')
	
	config.add_route('login', '/login')
	config.add_route('logout', '/logout')
	
	config.add_static_view(name='static', path='DCRequestAPI:static')
	
	config.scan('DCRequestAPI.views')
	return config.make_wsgi_app()
