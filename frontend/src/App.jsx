import React from 'react'
import { 
  Route,
  createBrowserRouter,
  createRoutesFromElements,
  RouterProvider
} from "react-router";
import AuthLayout from './layout/AuthLayout';
import SignUp from './page/SignUp';
import Login from './page/Login';
import Chat from './page/Chat';
import ProtectedLayout from './layout/ProtectedLayout';

const router = createBrowserRouter(
  createRoutesFromElements(
    <>
      <Route path="/" element={<AuthLayout/>}>
        <Route path="/" element={<SignUp/>}/>
        <Route path="/login" element={<Login/>}/>
      </Route>
      <Route path="/chat" element={<ProtectedLayout/>}>
        <Route path="" element={<Chat/>}/>      
      </Route>
    </>
  )
);

const App = () => {
  return (
    <RouterProvider router={router} />
  )
}

export default App
