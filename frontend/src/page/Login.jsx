import React, { useState } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import { logIn } from '../firebase/authFirebase';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await logIn(email, password);
      navigate("/chat");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form className="font-roboto my-5" onSubmit={handleLogin}>
        <div className="space-y-5">
          <input
            type="text"
            placeholder="Enter your email"
            className="w-full px-4 py-3 bg-gray-100 text-black"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            type="password"
            placeholder="Enter your password"
            className="w-full px-4 py-3 bg-gray-100 text-black"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button
            type="submit"
            className="px-4 py-3 w-full bg-[#e97363] text-white"
            disabled={loading}
          >
            {loading ? 'Loading...' : 'Login'}
          </button>
          {error && <p className="text-red-500">{error}</p>}
        </div>
      </form>
      <Link to="/" className="text-blue-500 hover:underline font-roboto">
        Don't have an account? Create one
      </Link>
    </div>
  );
};

export default Login;