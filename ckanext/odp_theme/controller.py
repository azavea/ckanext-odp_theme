
import datetime

import ckan.plugins as p
import ckan.model as model
from ckan.plugins import toolkit as tk
from ckan.common import c

from feedback_model import UnpublishedFeedback


class UnpublishedFeedbackController(p.toolkit.BaseController):
    controller = 'ckanext.odp_theme.controller:UnpublishedFeedbackController'

    def view_feedback(self, id):
        """Renders a page containing the feedback form and a list of feedback.
        """
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'for_view': True,
                   'auth_user_obj': c.userobj}
        data_dict = {'id': id}
        data = tk.request.POST
        session = context['session']
        try:
            c.pkg_dict = tk.get_action('package_show')(context, data_dict)
            c.pkg_revisions = tk.get_action('package_revision_list')(context,
                                                                     data_dict)
            c.pkg = context['package']
            if (tk.request.method == 'POST' and c.userobj and
                    c.userobj.sysadmin and 'delete' in data):
                # sysadmin can delete comments
                UnpublishedFeedback.get(id=data['id']).delete()
                session.commit()
                return tk.redirect_to(controller='package', action='read',
                                      id=c.pkg.name)
            if c.userobj:
                c.user_feedback = UnpublishedFeedback.get(dataset=c.pkg.id,
                                                          user=c.userobj.id)
                if not c.user_feedback:
                    c.user_feedback = UnpublishedFeedback()
                    c.user_feedback.dataset = c.pkg.id
                    c.user_feedback.user = c.userobj.id
                if tk.request.method == 'POST':  # INSERT/UPDATE/DELETE
                    if 'comment' in data and data['comment'].strip() != '':
                        setattr(c.user_feedback, 'comments', data['comment'])
                        c.user_feedback.modified = datetime.datetime.utcnow()
                        c.user_feedback.save()
                        session.add(c.user_feedback)
                    elif c.user_feedback.id:
                        c.user_feedback.delete()
                    session.commit()

            c.pkg_feedback = UnpublishedFeedback.get_for_package(c.pkg.id).all()
        except tk.NotAuthorized:
            tk.abort(401, tk._('Unauthorized to read package'))
        except tk.ObjectNotFound:
            tk.abort(404, tk._('Dataset not found'))

        #return tk.render('feedback/feedback.html')
        return tk.redirect_to(controller='package', action='read',
                              id=c.pkg.name)
