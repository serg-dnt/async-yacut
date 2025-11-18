from flask import abort, redirect, url_for, render_template
from http import HTTPStatus

from . import app, db
from .forms import URLForm, FilesForm
from .models import URLMap
from .utils import get_unique_short_id, upload_files_to_yandex_disk


@app.route('/', methods=['GET', 'POST'])
def index():
    form = URLForm()
    short_url = None
    if form.validate_on_submit():
        original_link = form.original_link.data
        if form.custom_id.data:
            short_id = form.custom_id.data
        else:
            short_id = get_unique_short_id()
        url_map = URLMap(original=original_link, short=short_id)
        db.session.add(url_map)
        db.session.commit()
        short_url = url_for(
            'redirect_to_original',
            short_id=short_id,
            _external=True
        )
    return render_template(
        'index.html',
        form=form,
        short_url=short_url,
        active_page='index'
    )


@app.route('/files', methods=['GET', 'POST'])
def files():
    form = FilesForm()
    file_links = None
    if form.validate_on_submit():
        files = form.files.data or []
        upload_results = upload_files_to_yandex_disk(files)
        file_links = []
        for filename, public_url in upload_results:
            short_id = get_unique_short_id()
            url_map = URLMap(original=public_url, short=short_id)
            db.session.add(url_map)
            db.session.commit()
            short_link = url_for(
                'redirect_to_original',
                short_id=short_id,
                _external=True
            )
            file_links.append((filename, short_link))
    return render_template(
        'files.html',
        form=form,
        file_links=file_links,
        active_page='files'
    )


@app.route('/<short_id>')
def redirect_to_original(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if url_map is None:
        abort(HTTPStatus.NOT_FOUND)
    return redirect(url_map.original)
