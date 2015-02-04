
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
        try:
            c.pkg_dict = tk.get_action('package_show')(context, data_dict)
            c.pkg_revisions = tk.get_action('package_revision_list')(context,
                                                                     data_dict)
            c.pkg = context['package']
            if c.userobj:
                c.user_feedback = UnpublishedFeedback.get(dataset=c.pkg.id,
                                                          user=c.userobj.id)
                if not c.user_feedback:
                    c.user_feedback = UnpublishedFeedback()
                    c.user_feedback.dataset = c.pkg.id
                    c.user_feedback.user = c.userobj.id
            if tk.request.method == 'POST':  # INSERT/UPDATE/DELETE
                data = tk.request.POST
                comment_fields = [('economic', 'economic_comment'),
                                  ('social', 'social_comment'),
                                  ('public-service', 'public_service_comment'),
                                  ('other', 'other_comment')]
                empty = True
                for form_name, db_name in comment_fields:
                    checkbox = 'checkbox-{}'.format(form_name)
                    if checkbox in data and data[checkbox]:
                        empty = False
                        if form_name not in data:
                            data[form_name] = ''
                        setattr(c.user_feedback, db_name, data[form_name])
                    else:
                        setattr(c.user_feedback, db_name, None)
                session = context['session']
                if not empty:
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
