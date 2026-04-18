from pathlib import Path


def test_base_template_csp_allows_googlevideo_connections():
    template = Path('youtube/templates/base.html').read_text(encoding='utf-8')
    assert "connect-src 'self' https://*.googlevideo.com;" in template


def test_embed_template_csp_allows_googlevideo_connections():
    template = Path('youtube/templates/embed.html').read_text(encoding='utf-8')
    assert "connect-src 'self' https://*.googlevideo.com;" in template
