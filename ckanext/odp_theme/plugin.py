
from collections import OrderedDict

import pylons

import ckan.plugins as plugins
import ckan.plugins.toolkit as tk


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

    def get_helpers(self):
        """Register odp_theme_* helper functions"""

        return {'odp_theme_most_recent_datasets': most_recent_datasets,
                'odp_theme_dataset_count': dataset_count,
                'odp_theme_groups': groups,
                'odp_theme_apps': apps}
