import React, { useState } from "react";
import { logOut } from '../firebase/authFirebase';
import { useNavigate } from "react-router-dom";

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState("");
  const navigate = useNavigate();

  const handleSendMessage = async (e) => {
    e.preventDefault();

    try {
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: "user", text: userInput },
        { sender: "assistant", text: "hello" },
      ]);
    } catch (error) {
      console.error(error);
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: "user", text: userInput },
        { sender: "assistant", text: "Unexpected Error Occurred" },
      ]);
    }
    setUserInput("");
  };

  const handleNewChat = () => {
    setMessages([]);
    setUserInput("");
  };

  const handleLogout = async () => {
    await logOut()
    navigate("/login")
  }

  return (
    <div className="font-roboto h-screen flex flex-col bg-gray-50">
      <div className="w-full p-4 sm:p-3 md:px-4 md:py-3 lg:px-10 lg:py-5 bg-[#e97363] text-white flex flex-row justify-between items-center gap-2 sm:gap-0">
        <div className="font-instrument italic text-2xl sm:text-3xl font-semibold">
          EmpathyBot
        </div>
        <div className="flex space-x-2 sm:space-x-3">
          <button
            className="bg-white hover:bg-gray-50 text-blue-500 px-3 sm:px-5 py-1.5 sm:py-2 rounded-xl text-sm sm:text-base"
            onClick={handleNewChat}
          >
            New
          </button>
          <button className="bg-white hover:bg-gray-50 text-blue-500 px-3 sm:px-5 py-1.5 sm:py-2 rounded-xl text-sm sm:text-base" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-2 sm:px-3 md:px-4 py-3 sm:py-5 w-full max-w-7xl mx-auto">
        <div className="w-full sm:w-11/12 md:w-4/5 lg:w-3/4 mx-auto">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${
                message.sender === "user" ? "justify-end" : "justify-start"
              } mb-3`}
            >
              <div
                className={`${
                  message.sender === "user"
                    ? "bg-gray-200 text-black"
                    : "bg-[#e97363] text-white"
                } p-2 sm:p-3 rounded-xl max-w-[75%] sm:max-w-md break-words text-sm sm:text-base`}
              >
                {message.text}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="w-full bg-white border-t border-gray-200 shadow-sm">
        <form
          className="w-full max-w-7xl mx-auto px-2 sm:px-3 md:px-4 py-3 flex items-center gap-2"
          onSubmit={handleSendMessage}
        >
          <div className="w-full sm:w-11/12 md:w-4/5 lg:w-3/4 mx-auto flex gap-2">
            <input
              type="text"
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              className="flex-1 px-3 sm:px-4 py-2 sm:py-3 bg-gray-100 text-black rounded-lg text-sm sm:text-base"
              placeholder="Type a message"
              required
            />
            <button
              type="submit"
              className="px-4 sm:px-6 py-2 sm:py-3 bg-[#e97363] text-white rounded-lg hover:bg-[#d66959] text-sm sm:text-base whitespace-nowrap"
            >
              Send
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Chat;
