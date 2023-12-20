import logging
log = logging.getLogger(__name__)

from pyramid.response import Response
from pyramid.renderers import render_to_response
from pyramid.view import (view_config, view_defaults)
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPSeeOther

from DCRequestAPI.lib.ElasticSearch.ES_Searcher import ES_Searcher

import pudb
import json



class IUPartsListView():
	def __init__(self, request):
		self.request = request
		self.uid = self.request.authenticated_userid
		
		self.roles = self.request.identity['dwb_roles']
		self.users_projects = self.request.identity['projects']
		


	@view_config(route_name='iupartslist', accept='text/html', renderer="DCRequestAPI:templates/help.pt")
	def IUPartsList(self):
		pudb.set_trace()
		
		
		es_searcher = ES_Searcher(search_params = {}, user_id = self.uid, users_projects = self.users_projects)
		es_searcher.paginatedSearch()
		
		
		pagecontent = {
			'pagetitle': 'API for requests on DiversityCollection database',
			'applicationurl': self.request.application_url
			
		}
		return pagecontent
