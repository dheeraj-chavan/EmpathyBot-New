import {getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut} from 'firebase/auth';
import firebase_app from './config';

const auth = getAuth(firebase_app);

export const signIn = async (email, password) => {
  try {
    const response = await createUserWithEmailAndPassword(auth, email, password);
    return response;
  } catch (e) {
    throw new Error(e);
  }
}

export const logIn = async (email, password) => {
  try {
    const response = await signInWithEmailAndPassword(auth, email, password);
    return response;
  } catch (e) {
    throw new Error(e);
  }
}

export const logOut = async () => {
  try {
    await signOut(auth);
  } catch (e) {
    throw new Error(e);
  }
}

export const getCurrentUser = () => {
  return auth.currentUser;
}