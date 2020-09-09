from django.shortcuts import render, redirect
from .models import *
from .forms import *
from posts.models import *
from posts.forms import *
from django.db.models import Q
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def mytimeline(request):
    me = request.user
    myprofile = Profile.objects.get(user=me)
    myposts = Post.objects.filter(Q(author=myprofile) | Q(wall=myprofile)).order_by('-id')
    print(myposts)

    context = {'myprofile': myprofile, 'myposts': myposts}
    return render(request, 'timeline/time-line.html', context)


@login_required
def myabout(request):
    me = request.user
    myprofile = Profile.objects.get(user=me)
    context = {'myprofile': myprofile, 'me': me}
    return render(request, 'timeline/about.html', context)


@login_required
def updateprofile(request):
    me = request.user
    myprofile = Profile.objects.get(user=request.user)

    form = ProfileForm(request.POST or None, instance=myprofile)

    if request.method == 'POST':

        if form.is_valid():
            form.save()
            return redirect('about')

    ppf = ProfilePic()
    cpf = CoverPic()

    if 'profile_image' in request.POST:
        ppf = ProfilePic(request.POST, request.FILES, instance=myprofile)
        if ppf.is_valid():
            ppf.save()
            return redirect('myupdate')

    if 'cover_image' in request.POST:
        cpf = CoverPic(request.POST, request.FILES, instance=myprofile)
        if cpf.is_valid():
            cpf.save()
            return redirect('myupdate')

    context = {'form': form, 'myprofile': myprofile, 'cpf': cpf, 'ppf': ppf}

    return render(request, 'timeline/edit-profile-basic.html', context)


@login_required
def friends(request):
    me = request.user
    allprofile = Profile.objects.all().exclude(user=me)
    myprofile = Profile.objects.get(user=me)

    blocker = Relation.objects.filter(sender=myprofile, block='block')
    bck = []
    for i in blocker:
        bck.append(i.receiver)

    blockeater = Relation.objects.filter(receiver=myprofile, block='block')
    bek = []
    for j in blockeater:
        bek.append(j.sender)

    rel_sender = myprofile

    from_send = Relation.objects.filter(sender=myprofile, status='send')
    to_send = Relation.objects.filter(
        receiver=myprofile, status='send')  # => 0

    relation_sender = []
    relation_receiver = []

    for item in from_send:
        relation_receiver.append(item.receiver.user)

    for item in to_send:
        relation_sender.append(item.sender.user)

    context = {'ap': allprofile, 'from_send': from_send, 'to_send': to_send,
               'rs': relation_sender, 'rc': relation_receiver, 'myprofile': myprofile,  'bck': bck, 'bek': bek}
    return render(request, 'timeline/people-nearby.html', context)


@login_required
def sendrequest(request):

    if request.method == 'POST':
        me = request.user   #me (request-sender) to (request-receiver)
        myprofile = Profile.objects.get(user=me)
        pid = request.POST.get('profile_pk')
        rel_receiver = Profile.objects.get(pk=pid)
        rel = Relation.objects.create(
            sender=myprofile, receiver=rel_receiver, status='send')
        try:

            Notification.objects.get(
                not_sender=myprofile, not_receiver=rel_receiver, status='friend').delete()

        except:
            Notification.objects.create(
                not_sender=myprofile, not_receiver=rel_receiver, status='friend')

        return redirect('peoples')

    return redirect('peoples')


@login_required
def acceptrequest(request):
    if request.method == 'POST':
        me = request.user
        myprofile = Profile.objects.get(user=me)
        pid = request.POST.get('profile_pk')
        sender = Profile.objects.get(pk=pid)

        myprofile.friends.add(sender.user)
        sender.friends.add(myprofile.user)

        obj = Relation.objects.get(
            sender=sender, receiver=myprofile, status='send')
        obj.delete()
        not_f = Notification.objects.get(
            not_sender=sender, not_receiver=myprofile, status='friend')
        not_f.delete()
        Notification.objects.create(
            not_sender=myprofile, not_receiver=sender, status='accept')

        return redirect('peoples')

    return redirect('peoples')


@login_required
def removefriend(request):
    if request.method == 'POST':
        me = request.user
        myprofile = Profile.objects.get(user=me)
        pid = request.POST.get('profile_pk')
        cancel = Profile.objects.get(pk=pid)

        myprofile.friends.remove(cancel.user)
        cancel.friends.remove(myprofile.user)

        return redirect('peoples')

    return redirect('peoples')


@login_required
def cancelrequest(request):
    if request.method == 'POST':
        me = request.user
        myprofile = Profile.objects.get(user=me)
        pid = request.POST.get('profile_pk')
        cancel = Profile.objects.get(pk=pid)

        rel = Relation.objects.get(
            sender=myprofile, receiver=cancel, status='send')

        rel.delete()

        return redirect('peoples')

    return redirect('peoples')


@login_required
def ignorerequest(request):
    if request.method == 'POST':
        me = request.user
        myprofile = Profile.objects.get(user=me)
        pid = request.POST.get('profile_pk')
        ignore = Profile.objects.get(pk=pid)

        rel = Relation.objects.get(
            sender=ignore, receiver=myprofile, status='send')

        rel.delete()

        return redirect('peoples')

    return redirect('peoples')


@login_required
def blockfriend(request):

    if 'block' in request.POST:
        me = request.user
        myprofile = Profile.objects.get(user=me)
        pid = request.POST.get('profile_pk')
        block = Profile.objects.get(pk=pid)

        Relation.objects.create(
            sender=myprofile, receiver=block, block='block')

        try:
            myprofile.friends.remove(block.user)
            block.friends.remove(myprofile.user)
        except:
            print('')
        return redirect('peoples')

    return redirect('peoples')


@login_required
def unblock(request):
    me = request.user
    myprofile = Profile.objects.get(user=me)
    blocked = Relation.objects.filter(sender=myprofile, block='block')
    bk = []
    for b in blocked:
        bk.append(b.receiver)

    if 'unblock' in request.POST:
        pid = request.POST.get('profile_pk')
        unblocks = Profile.objects.get(pk=pid)
        rel = Relation.objects.get(
            sender=myprofile, receiver=unblocks, block='block')
        rel.delete()

        return redirect('ub')

    context = {'bk': bk, 'myprofile': myprofile}
    return render(request, 'timeline/unblock.html', context)


@login_required
def detailprofile(request, profile_slug):
    me = request.user
    myprofile = Profile.objects.get(user=me)
    profile = Profile.objects.get(slug=profile_slug)
    posts = Post.objects.filter(
        Q(author=profile) | Q(wall=profile)).order_by('-id')
    post_f = PostForm(initial={'visibility': 'public',
                               'comment_choice': 'allow-comment'})

    if 'submit_post_friend' in request.POST:
        post_f = PostForm(request.POST, request.FILES)
        if post_f.is_valid():
            instance = post_f.save(commit=False)
            instance.author = myprofile
            instance.wall = profile
            instance.save()
            post_f = PostForm()
            return redirect('newsfeed')

    context = {'profile': profile, 'posts': posts,
               'myprofile': myprofile, 'pf': post_f}
    return render(request, 'timeline/detail-profile.html', context)
