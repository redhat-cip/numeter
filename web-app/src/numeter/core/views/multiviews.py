from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required()
def multiviews_index(request):
	return render(request, 'multiviews.html', {})
