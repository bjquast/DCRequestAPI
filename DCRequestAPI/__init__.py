from pyramid.config import Configurator
from pyramid.renderers import JSONP

from pyramid.authentication import SessionAuthenticationPolicy
from pyramid_beaker import session_factory_from_settings

from dwb_authentication.security import SecurityPolicy

# recreate the session db each time the server is started
# code might be kept in memory, how can i prevent that?
from dwb_authentication.setup_session_db.create_database import SessionDBSetup


def main(global_config, **settings):
	session_db = SessionDBSetup()
	del session_db
	
	config = Configurator(settings=settings)
	
	config.include('pyramid_beaker')
	session_factory = session_factory_from_settings(settings)
	config.set_security_policy(SecurityPolicy())
	
	config.include('pyramid_chameleon')
	config.add_renderer('jsonp', JSONP(param_name='callback'))
	
	config.add_route('iupartslist', '/list')
	config.add_route('export_csv', '/export/csv')
	config.add_route('aggregation', '/aggregation')
	#config.add_route('hierarchy_aggregation', '/hierarchy_aggregation/{hierarchy_name}')
	config.add_route('hierarchies', '/hierarchies')
	config.add_route('hierarchy_remove_path', '/hierarchy/remove_path/{hierarchy_name}')
	config.add_route('aggs_suggestions', '/aggs_suggestions')
	config.add_route('help', '/')
	
	config.add_route('login', '/login')
	config.add_route('logout', '/logout')
	
	config.add_route('get_field_type', '/get_field_type/{fieldname}')
	
	config.add_static_view(name='static', path='DCRequestAPI:static')
	
	config.scan('DCRequestAPI.views')
	return config.make_wsgi_app()
