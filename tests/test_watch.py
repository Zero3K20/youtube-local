from youtube import watch


def test_add_video_title_to_format_urls_keeps_direct_urls():
    formats = [
        {
            'url': 'https://rr2---sn-8xgp1vo-3uhs.googlevideo.com/videoplayback?foo=bar',
            'ext': 'mp4',
        },
        {
            'url': 'https://rr2---sn-8xgp1vo-3uhs.googlevideo.com/videoplayback?baz=qux',
            'ext': None,
        },
    ]

    watch.add_video_title_to_format_urls(formats, 'a:b?')

    assert formats[0]['url'].startswith('https://')
    assert not formats[0]['url'].startswith('/https://')
    assert '/videoplayback/name/a-b.mp4?' in formats[0]['url']
    assert '/videoplayback/name/a-b?' in formats[1]['url']
