import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { signIn } from "../firebase/authFirebase";

const SignUp = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSignUp = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await signIn(email, password);
      navigate("/login");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form className="font-roboto my-5" onSubmit={handleSignUp}>
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
            {loading ? "Loading..." : "Create your account"}
          </button>
          {error && <p className="text-red-500">{error}</p>}
        </div>
      </form>
      <Link to="/login" className="text-blue-500 hover:underline font-roboto">
        Already have an account?
      </Link>
    </div>
  );
};

export default SignUp;
