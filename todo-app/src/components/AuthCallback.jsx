import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const AuthCallback = ({ onLogin }) => {
  const navigate = useNavigate();

  useEffect(() => {
    // Token is now in HttpOnly cookie, not in URL
    // Just fetch user data - the cookie will be sent automatically
    const fetchUser = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/auth/me`, {
          credentials: 'include', // Send HttpOnly cookie with request
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          const user = await response.json();
          localStorage.setItem('user', JSON.stringify(user));
          onLogin(user);
          navigate('/');
        } else {
          console.error('Failed to fetch user');
          navigate('/login');
        }
      } catch (error) {
        console.error('Error fetching user:', error);
        navigate('/login');
      }
    };

    fetchUser();
  }, [navigate, onLogin]);

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh',
      flexDirection: 'column',
    }}>
      <div className="spinner"></div>
      <p style={{ marginTop: '20px' }}>Completing sign in...</p>
    </div>
  );
};

export default AuthCallback;
