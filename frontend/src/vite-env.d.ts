/// <reference types="vite/client" />

export {};

declare global {
    interface CredentialResponse {
        credential: string;
        select_by: string;
        clientId?: string;
    }

    interface GoogleAccountsId {
        initialize: (config: {
            client_id: string;
            callback: (response: CredentialResponse) => void;
            auto_select?: boolean;
            cancel_on_tap_outside?: boolean;
        }) => void;
        renderButton: (
            parent: HTMLElement,
            options: {
                theme?: "outline" | "filled_blue" | "filled_black";
                size?: "large" | "medium" | "small";
                type?: "standard" | "icon";
                text?: "signin_with" | "signup_with" | "continue_with" | "signin";
                shape?: "rectangular" | "pill" | "circle" | "square";
                width?: number | string;
            }
        ) => void;
        prompt: () => void;
    }

    interface Google {
        accounts: {
            id: GoogleAccountsId;
        };
    }

    interface Window {
        google?: Google;
    }
}
