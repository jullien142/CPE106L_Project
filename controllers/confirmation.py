from community_skill_exchange.models import Match, Confirmation, MatchHistory, Cancellation
from community_skill_exchange.database import SessionLocal
from datetime import datetime, timedelta

def confirm_match(match_id, accepted, session=None):
    close_session = False
    if session is None:
        session = SessionLocal()
        close_session = True
    try:
        match = session.query(Match).filter_by(id=match_id).first()
        if not match:
            return None
        confirmation = session.query(Confirmation).filter_by(match_id=match_id).first()
        if not confirmation:
            confirmation = Confirmation(match_id=match_id)
            session.add(confirmation)
        confirmation.status = 'accepted' if accepted else 'declined'
        confirmation.responded_at = datetime.utcnow()
        match.status = 'confirmed' if accepted else 'cancelled'
        match.confirmed_at = datetime.utcnow() if accepted else None
        # Add to history
        history = MatchHistory(match_id=match_id, status=match.status)
        session.add(history)
        session.commit()
        return confirmation
    finally:
        if close_session:
            session.close()

def auto_cancel_expired_matches(session=None):
    close_session = False
    if session is None:
        session = SessionLocal()
        close_session = True
    try:
        now = datetime.utcnow()
        expired_matches = session.query(Match).filter(
            Match.status == 'pending',
            Match.expires_at != None,
            Match.expires_at < now
        ).all()
        for match in expired_matches:
            match.status = 'expired'
            confirmation = session.query(Confirmation).filter_by(match_id=match.id).first()
            if confirmation:
                confirmation.status = 'expired'
                confirmation.responded_at = now
            history = MatchHistory(match_id=match.id, status='expired')
            session.add(history)
        session.commit()
        return expired_matches
    finally:
        if close_session:
            session.close()

def resubmit_request(request, session=None):
    close_session = False
    if session is None:
        session = SessionLocal()
        close_session = True
    try:
        request.status = 'pending'
        session.commit()
        return request
    finally:
        if close_session:
            session.close() 