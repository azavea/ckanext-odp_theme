
import ckan.plugins as plugins
import ckan.plugins.toolkit as tk


def most_recent_datasets():
    """Return a list of recent datasets."""

    # the current_package_list_with_resources action returns private resources
    # which need to be filtered
    datasets = tk.get_action('current_package_list_with_resources')({},
                        {'limit': 100})

    return filter(lambda ds: not ds['private'], datasets)[:10]


def dataset_count():
    """Return a count of all datasets"""

    return len(tk.get_action('package_list')({}, {}))


def groups():
    """Return a list of groups"""

    return tk.get_action('group_list')({}, {'all_fields': True})


class ODPThemePlugin(plugins.SingletonPlugin):
    """OpenDataPhilly theme plugin.

    """

    plugins.implements(plugins.IConfigurer)

    plugins.implements(plugins.ITemplateHelpers)

    def update_config(self, config):
        """Register this plugin's template dir"""

        tk.add_template_directory(config, 'templates')

    def get_helpers(self):
        """Register odp_theme_* helper functions"""

        return {'odp_theme_most_recent_datasets': most_recent_datasets,
                'odp_theme_dataset_count': dataset_count,
                'odp_theme_groups': groups}
