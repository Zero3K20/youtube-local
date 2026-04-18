import urllib.parse

from youtube import util, watch

TEST_TITLE_WITH_INVALID_CHARS = 'a:b?/\\*<>|"'


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

    title = TEST_TITLE_WITH_INVALID_CHARS
    expected_name = urllib.parse.quote(util.to_valid_filename(title))
    watch.add_video_title_to_format_urls(formats, title)

    assert formats[0]['url'].startswith('https://')
    assert not formats[0]['url'].startswith('/https://')
    assert '/videoplayback/name/' + expected_name + '.mp4?' in formats[0]['url']
    assert '/videoplayback/name/' + expected_name + '?' in formats[1]['url']


def test_add_video_title_to_format_urls_handles_missing_title():
    formats = [
        {
            'url': 'https://rr2---sn-8xgp1vo-3uhs.googlevideo.com/videoplayback?foo=bar',
            'ext': 'mp4',
        },
    ]

    watch.add_video_title_to_format_urls(formats, None)
    assert '/videoplayback/name/_.mp4?' in formats[0]['url']

    formats = [
        {
            'url': 'https://rr2---sn-8xgp1vo-3uhs.googlevideo.com/videoplayback?foo=bar',
            'ext': 'mp4',
        },
    ]
    watch.add_video_title_to_format_urls(formats, '')
    assert '/videoplayback/name/_.mp4?' in formats[0]['url']
