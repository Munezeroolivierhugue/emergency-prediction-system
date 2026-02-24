import React from "react";
import AuthLayout from "../components/AuthLayout";
import RegisterForm from "../components/RegisterForm";

const Register = () => {
    return (
        <AuthLayout
            title="Create Account"
            subtitle="Join the emergency response network today"
        >
            <RegisterForm />
        </AuthLayout>
    );
};

export default Register;
