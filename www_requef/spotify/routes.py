from www_requef.config import SPOTIFY_REDIRECT_URI
from www_requef.main import get_templates
from www_requef.spotify.dependencies import get_client
from www_requef.spotify.client import SpotifyClient
from urllib.parse import urlencode
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates


router = APIRouter()


@router.get("/error")
async def auth_error(req: Request, t: Jinja2Templates = Depends(get_templates)):
    return t.TemplateResponse("spotify/login_fail.html", {"request": req}, status_code = 403)


@router.get("/success")
async def auth_success(req: Request, t: Jinja2Templates = Depends(get_templates)):
    return t.TemplateResponse("spotify/login_success.html", {"request": req})


@router.get("/")
async def login(_: Request, client: SpotifyClient = Depends(get_client)):
    if client.authorized:
        return RedirectResponse("/spotify/success")
    
    client.regenerate_state()

    params = {
        "response_type": "code",
        "client_id": client.client_id,
        "scope": "user-read-currently-playing",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "state": client.state
    }
    return RedirectResponse(f"https://accounts.spotify.com/authorize?{urlencode(params)}")


@router.get("/callback")
async def callback(_: Request, 
                   code: str = "", 
                   state: str = "", 
                   client: SpotifyClient = Depends(get_client)):
    if client.authorized:
        # Returning error if client is already authorized to say that the 
        # authorization is no longer possible (even for others)
        return RedirectResponse("/spotify/error")

    # Reject all requests with incorrect state/code.
    if state != client.state:
        return RedirectResponse("/spotify/error")
    if not code:
        return RedirectResponse("/spotify/error")

    # Request access and refresh tokens.
    if not client.request_tokens(code):
        return RedirectResponse("/spotify/error")

    return RedirectResponse("/spotify/success")


@router.get("/track", response_class=HTMLResponse)
async def current_track(client: SpotifyClient = Depends(get_client)):
    if not client.authorized:
        return ""
    
    track = await client.get_current_track()
    if track:
        track_id = track["track_id"]
        track_name = track["track_name"]
        artist_names = track["artist_names"]
        album_cover_url = track["album_cover_url"]
        return (
            f"<figure id='current-track-container-{track_id}' class='current-track-container center'>"
                f"<img class='current-track-album-cover' draggable='false' src='{album_cover_url}' alt='Current Track Album Cover'>"
                "<figcaption class='current-track-info'>"
                    "<a href='https://open.spotify.com/user/31zilo7ssyl7kmqobuq4x447tqau?si=8a0dc05095a14e5b' "
                    "target='_blank'><strong class='nickname-normal'>requef</strong></a> is now listening to "
                    f"<strong>{track_name}</strong> by <strong>{artist_names}</strong>"
                "</figcaption>"
            "</figure>"
        )
    
    return ""
