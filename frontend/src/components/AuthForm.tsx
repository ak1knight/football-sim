import React, { useState } from "react";
import { observer } from "mobx-react-lite";
import { userStore } from "../stores/UserStore";
import { Button } from "./ui/Button";
import { ErrorMessage } from "./ui/ErrorMessage";
import { Card } from "./ui/Card";

type Mode = "login" | "register";

export const AuthForm = observer(() => {
  const [mode, setMode] = useState<Mode>("login");
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
    firstName: "",
    lastName: "",
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const validate = () => {
    if (!form.username || !form.password) return "Username and password required";
    if (mode === "register") {
      if (!form.email) return "Email required";
      if (form.password.length < 6) return "Password must be at least 6 characters";
      if (form.password !== form.confirmPassword) return "Passwords do not match";
    }
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const error = validate();
    if (error) {
      userStore.setError(error);
      return;
    }
    setLoading(true);
    if (mode === "login") {
      await userStore.login(form.username, form.password);
    } else {
      await userStore.register(
        form.username,
        form.email,
        form.password,
        form.firstName,
        form.lastName
      );
    }
    setLoading(false);
  };

  const switchMode = () => {
    setMode(mode === "login" ? "register" : "login");
    userStore.setError(null);
  };

  return (
    <div className="flex justify-center items-center min-h-[60vh]">
      <Card className="w-full max-w-md p-8 shadow-lg bg-base-100 border border-base-300">
        <h2 className="text-3xl font-semibold mb-6 text-center text-primary">
          {mode === "login" ? "Sign In" : "Create Account"}
        </h2>
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-base-content mb-1" htmlFor="username">
              Username
            </label>
            <input
              className="block w-full px-4 py-2 border border-secondary-600 rounded-lg bg-secondary-700 placeholder-secondary-200 focus:outline-none focus:ring-2 focus:ring-secondary focus:border-secondary transition"
              id="username"
              name="username"
              placeholder="Username"
              value={form.username}
              onChange={handleChange}
              autoComplete="username"
            />
          </div>
          {mode === "register" && (
            <div>
              <label className="block text-sm font-medium text-base-content mb-1" htmlFor="email">
                Email
              </label>
              <input
                className="block w-full px-4 py-2 border border-secondary-600 rounded-lg bg-secondary-700 placeholder-secondary-200 focus:outline-none focus:ring-2 focus:ring-secondary focus:border-secondary transition"
                id="email"
                name="email"
                placeholder="Email"
                type="email"
                value={form.email}
                onChange={handleChange}
                autoComplete="email"
              />
            </div>
          )}
          <div>
            <label className="block text-sm font-medium text-base-content mb-1" htmlFor="password">
              Password
            </label>
            <input
              className="block w-full px-4 py-2 border border-secondary-600 rounded-lg bg-secondary-700 placeholder-secondary-200 focus:outline-none focus:ring-2 focus:ring-secondary focus:border-secondary transition"
              id="password"
              name="password"
              placeholder="Password"
              type="password"
              value={form.password}
              onChange={handleChange}
              autoComplete={mode === "login" ? "current-password" : "new-password"}
            />
          </div>
          {mode === "register" && (
            <>
              <div>
                <label className="block text-sm font-medium text-base-content mb-1" htmlFor="confirmPassword">
                  Confirm Password
                </label>
                <input
                  className="block w-full px-4 py-2 border border-secondary-600 rounded-lg bg-secondary-700 placeholder-secondary-200 focus:outline-none focus:ring-2 focus:ring-secondary focus:border-secondary transition"
                  id="confirmPassword"
                  name="confirmPassword"
                  placeholder="Confirm Password"
                  type="password"
                  value={form.confirmPassword}
                  onChange={handleChange}
                  autoComplete="new-password"
                />
              </div>
              <div className="flex gap-3">
                <div className="flex-1">
                  <label className="block text-sm font-medium text-base-content mb-1" htmlFor="firstName">
                    First Name
                  </label>
                  <input
                    className="block w-full px-4 py-2 border border-secondary-600 rounded-lg bg-secondary-700 placeholder-secondary-200 focus:outline-none focus:ring-2 focus:ring-secondary focus:border-secondary transition"
                    id="firstName"
                    name="firstName"
                    placeholder="First Name"
                    value={form.firstName}
                    onChange={handleChange}
                    autoComplete="given-name"
                  />
                </div>
                <div className="flex-1">
                  <label className="block text-sm font-medium text-base-content mb-1" htmlFor="lastName">
                    Last Name
                  </label>
                  <input
                    className="block w-full px-4 py-2 border border-secondary-600 rounded-lg bg-secondary-700 placeholder-secondary-200 focus:outline-none focus:ring-2 focus:ring-secondary focus:border-secondary transition"
                    id="lastName"
                    name="lastName"
                    placeholder="Last Name"
                    value={form.lastName}
                    onChange={handleChange}
                    autoComplete="family-name"
                  />
                </div>
              </div>
            </>
          )}
          {userStore.error && <ErrorMessage message={userStore.error} />}
          <Button type="submit" className="w-full mt-2" disabled={loading}>
            {loading
              ? "Please wait..."
              : mode === "login"
              ? "Sign In"
              : "Register"}
          </Button>
        </form>
        <div className="mt-6 text-center">
          <button
            type="button"
            className="text-primary hover:underline font-medium"
            onClick={switchMode}
          >
            {mode === "login"
              ? "Don't have an account? Register"
              : "Already have an account? Sign In"}
          </button>
        </div>
      </Card>
    </div>
  );
});