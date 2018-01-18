from pyquery import PyQuery

if __name__ == '__main__':
    q = PyQuery(open('v2ex.html').read())

    print q('title').text()

    for each in q('div.inner>a').items():
        print 1, each.attr.href

    for each in q('#Tabs>a[]').items():
        print 2, each.attr.href

    for each in q('.cell>a[href^="/go/"]'):
        print 3, each.attr.href

    for each in q('cell a[href^="/go/"]'):
        print 4, each.attr.href

    for each in q('span.item_title>a[href^="/t/"]'):
        print 5, each.html

    for each in q('img.avatar').items():
        print 6, each.attr.src

    for each in q('a>img.avatar').items():
        print 6, each.attr.src
