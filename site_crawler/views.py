import asyncio
from django import forms
from django.conf import settings
from django.http import HttpRequest
from django.shortcuts import render
from django.utils.decorators import classonlymethod
from django.views import View

from site_crawler.crawl_lib import Crawler


class CrawlerForm(forms.Form):
    site_url = forms.URLField(label='Site url', max_length=1000)


class CrawlView(View):
    @classonlymethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        view._is_coroutine = asyncio.coroutines._is_coroutine
        return view

    async def get(self, request: HttpRequest):
        context = dict()
        if 'site_url' in request.GET:
            form = CrawlerForm(request.GET)
            if form.is_valid():
                crawler = Crawler(url=form.data['site_url'])
                context['urls'] = await crawler.get_hrefs_recursively(
                    max_depth=settings.MAX_HREF_CRAWL_DEPTH,
                )
        else:
            form = CrawlerForm()

        context['form'] = form
        return render(request, 'site_crawler.html', context)
