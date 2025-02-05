import React from "react";
import { Outlet } from "react-router-dom";
import BannerImg from "../assets/banner-singup.jpg";

const AuthLayout = () => {
  return (
    <div className="font-instrument flex flex-col md:flex-row w-full h-screen bg-white">
      <div className="w-full md:w-[60%] p-5 md:p-8 lg:p-10 flex flex-col justify-center">
        <div>
          <div className="mt-10 mb-5 font-bold italic text-4xl text-[#e97363]">
            EmpathyBot
          </div>
          <div className="text-5xl w-[90%]">
            Your Caring and Supportive AI Companion for Every Emotional Need
          </div>
        </div>
        <div className="my-5">
          <Outlet />
        </div>
      </div>
      <div className="flex-1 bg-white">
        <img
          src={BannerImg}
          className="w-full h-full object-cover object-center"
        />
      </div>
    </div>
  );
};

export default AuthLayout;
