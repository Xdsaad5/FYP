SECRET_KEY = "BSEF20A032"
FLASK_DEBUG = True
ENV = True
SENDER_EMAIL = 'saad17mughal@gmail.com'
SENDER_PASSWORD = 'lahore@17'
SUBJECT_EMAIL = "OTP"
EMAIL_PASSWORD = 'wcse mvkc ekrf bjrf'
USER_COLLECTION = 'User'
COMMUNITY_COLLECTION = 'Community'
JOIN_COMMUNITIES_COLLECTION = 'JOIN_COMMUNITIES'
AVAILABLE_DRIVERS = 'AvailableDrivers'
BOOKED_RIDES = 'Booked_Ride_Details'

SESSION_TYPE = 'filesystem'  # Options include 'filesystem', 'redis', 'memcached', etc.
SESSION_PERMANENT = False
SESSION_USE_SIGNER = True  # This will add an additional layer of security.
SESSION_KEY_PREFIX = 'route_mate:'  # Optional, but recommended for distinguishing your app's sessions.

