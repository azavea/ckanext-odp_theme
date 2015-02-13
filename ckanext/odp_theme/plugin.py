
from collections import OrderedDict

import pylons

from jinja2 import Undefined

import ckan.plugins as plugins
import ckan.plugins.toolkit as tk

from ckan.lib.activity_streams import \
    activity_stream_string_functions as activity_streams

from feedback_model import init_db, UnpublishedFeedback

def most_recent_datasets(num=3):
    """Return a list of recent datasets."""

    # the current_package_list_with_resources action returns private resources
    # which need to be filtered
    datasets = tk.get_action('current_package_list_with_resources')({},
                             {'limit': 100})

    return filter(lambda ds: not ds['private'], datasets)[:num]


def apps(featured_only=True):
    """Return apps for all datasets."""

    apps = tk.get_action('related_list')({}, {'type_filter': 'application',
                                              'featured': featured_only})

    return apps


def dataset_count():
    """Return a count of all datasets"""

    return len(tk.get_action('package_list')({}, {}))


def groups():
    """Return a list of groups"""

    return tk.get_action('group_list')({}, {'all_fields': True})


def user_feedback(pkgid, userid):
    """Return user feedback for a dataset"""

    if isinstance(userid, Undefined):
        return None
    feedback = UnpublishedFeedback.get(dataset=pkgid, user=userid)
    if feedback is None:
        feedback = UnpublishedFeedback()
    return feedback


def feedback_for_pkg(pkgid):
    """Return all feedback for a dataset"""

    return UnpublishedFeedback.get_for_package(pkgid).all()


# monkeypatch activity streams
activity_streams['changed group'] = (
    lambda c, a: tk._("{actor} updated the topic {group}")
)

activity_streams['deleted group'] = (
    lambda c, a: tk._("{actor} deleted the topic {group}")
)

activity_streams['new group'] = (
    lambda c, a: tk._("{actor} created the topic {group}")
)


class ODPSearchPlugin(plugins.SingletonPlugin):
    """
    This plugin sets the translation field for facets so that the items of
    the facet appear as "Published" and "Unpublished" instead of "true" and
    "false."

    """

    plugins.implements(plugins.IPackageController, inherit=True)

    def read(self, entity):
        pass

    def create(self, entity):
        pass

    def edit(self, entity):
        pass

    def authz_add_role(self, object_role):
        pass

    def authz_remove_role(self, object_role):
        pass

    def delete(self, entity):
        pass

    def after_search(self, search_results, search_params):
        return search_results

    def before_view(self, pkg_dict):
        c = pylons.c
        c.translated_fields = {}
        c.translated_fields[('published', 'false')] = 'Unpublished'
        c.translated_fields[('published', 'true')] = 'Published'
        return pkg_dict

    def before_index(self, pkg_dict):
        """Force the published extra to be indexed if it is not set."""
        pkg_dict['published'] = pkg_dict.get('published', 'true')
        return pkg_dict


class ODPThemePlugin(ODPSearchPlugin):
    """OpenDataPhilly theme plugin.

    """

    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IFacets)
    plugins.implements(plugins.IRoutes)

    def dataset_facets(self, facets_dict, package_type):
        """Add Published to the list of facets shown on the search page"""

        new_facets_dict = OrderedDict()
        new_facets_dict['published'] = tk._('Published')
        for key, value in facets_dict.items():
            new_facets_dict[key] = value
        if 'groups' in new_facets_dict:
            new_facets_dict['groups'] = tk._('Topics')
        return new_facets_dict

    def group_facets(self, facets_dict, group_type, package_type):
        if 'groups' in facets_dict:
            facets_dict['groups'] = tk._('Topics')
        return facets_dict

    def organization_facets(self, facets_dict, organization_type,
                            package_type):
        if 'groups' in facets_dict:
            facets_dict['groups'] = tk._('Topics')
        return facets_dict

    def update_config(self, config):
        """Register this plugin's template dir"""

        tk.add_template_directory(config, 'templates')

        # this adds directories to make public so we can include custom CSS
        # and javascript.
        # see http://docs.ckan.org/en/latest/theming/fanstatic.html
        tk.add_public_directory(config, 'public')
        tk.add_resource('fanstatic', 'odp_theme')
        init_db()

    def get_helpers(self):
        """Register odp_theme_* helper functions"""

        return {'odp_theme_most_recent_datasets': most_recent_datasets,
                'odp_theme_dataset_count': dataset_count,
                'odp_theme_groups': groups,
                'odp_theme_apps': apps,
                'unpublished_count': UnpublishedFeedback.count_for_package,
                'user_feedback': user_feedback,
                'feedback_for_pkg': feedback_for_pkg}

    def before_map(self, map):
        return map

    def after_map(self, map):
        unpublished_feedback_controller = 'ckanext.odp_theme.controller:UnpublishedFeedbackController'
        unpublished_report_controller = 'ckanext.odp_theme.controller:UnpublishedReportController'

        map.connect('view_feedback', '/dataset/{id}/feedback', action='view_feedback',
                    controller=unpublished_feedback_controller)
        map.connect('view_org', '/unpublished_report/{org_id}', action='view_org',
                    controller=unpublished_report_controller)
        return map
