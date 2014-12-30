from __future__ import absolute_import, division, unicode_literals

from django.views.generic import TemplateView

from .models import Post, post_upload_to


class SignS3TemplateView(
    TemplateView
):
    template_name = 'yaga/sign_s3.html'

    def get_context_data(self, **kwargs):
        context = super(SignS3TemplateView, self).get_context_data(**kwargs)

        post = Post.objects.filter(
            user=self.request.user
        )[0]

        sign_s3 = post.sign_s3()
        post.attachment = post_upload_to(post)
        post.save()

        context['sign_s3'] = sign_s3
        context['post'] = post

        return context
