from flask import Blueprint, jsonify, request
from ..scripts.fb_script import FacebookPoster
from ..scripts.twitter_script import TwitterPoster
from ..scripts.instagram_script import InstagramPoster
from ..scripts.linkedin_script import LinkedInPoster

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/status')
def status():
    """Check connection status for platforms"""
    platform = request.args.get('platform', '').lower()
    result = {}

    try:
        if platform == 'facebook' or not platform:
            try:
                fb_poster = FacebookPoster()
                fb_token_valid = fb_poster.verify_token()
                fb_page_access = fb_poster.verify_page_access() if fb_token_valid else False

                fb_page_name = None
                if fb_page_access:
                    page_result = fb_poster._request(fb_poster.page_id)
                    if page_result:
                        fb_page_name = page_result.get('name')

                result['facebook'] = {
                    'token_valid': fb_token_valid,
                    'page_access': fb_page_access,
                    'page_id': fb_poster.page_id,
                    'page_name': fb_page_name
                }
            except Exception as e:
                result['facebook'] = {'token_valid': False, 'page_access': False, 'error': str(e)}

        if platform == 'twitter' or not platform:
            try:
                tw_poster = TwitterPoster()
                tw_valid = tw_poster.verify_credentials()
                tw_username = None
                if tw_valid:
                    try:
                        me = tw_poster.client.get_me()
                        if getattr(me, 'data', None):
                            tw_username = getattr(me.data, 'username', None) or (me.data.get('username') if isinstance(me.data, dict) else None)
                    except Exception:
                        pass

                result['twitter'] = {'credentials_valid': tw_valid, 'username': tw_username}
            except Exception as e:
                result['twitter'] = {'credentials_valid': False, 'error': str(e)}

        if platform == 'instagram' or not platform:
            try:
                ig_poster = InstagramPoster()
                ig_token_ok = ig_poster and ig_poster.access_token is not None
                ig_account_ok = False
                ig_username = None
                ig_account_name = None

                if ig_token_ok:
                    account_info = ig_poster.get_account_info()
                    if account_info:
                        ig_account_ok = True
                        ig_username = account_info.get('username')
                        ig_account_name = account_info.get('name')

                result['instagram'] = {
                    'token_valid': ig_token_ok,
                    'account_id': getattr(ig_poster, 'ig_id', None),
                    'account_access': ig_account_ok,
                    'username': ig_username,
                    'account_name': ig_account_name
                }
            except Exception as e:
                result['instagram'] = {'token_valid': False, 'account_access': False, 'error': str(e)}

        if platform == 'linkedin' or not platform:
            try:
                li_poster = LinkedInPoster()
                li_token_valid = li_poster.verify_credentials()
                result['linkedin'] = {
                    'credentials_valid': li_token_valid,
                    'person_id': getattr(li_poster, 'person_id', None)
                }
            except Exception as e:
                result['linkedin'] = {'credentials_valid': False, 'error': str(e)}

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'SocMed Poster'})
