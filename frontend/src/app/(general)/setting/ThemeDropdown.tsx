import { BsChevronDown } from 'react-icons/bs';

import { enabledThemes, useTheme } from '@/logic/contexts.ts';
import { capitalizeFirstLetter } from '@/utils.ts';

export function ThemeDropdown() {
    const { theme, setTheme } = useTheme();

    return (
        <div className="dropdown">
            <div tabIndex={0} role="button" className="btn btn-sm bg-base-100 border-base-300 text-base-content">
                {theme}
                <BsChevronDown />
            </div>
            <ul
                tabIndex={0}
                className="menu menu-md dropdown-content bg-base-100 rounded-box z-[10] w-52 p-2 shadow-2xl"
            >
                {enabledThemes.map((item) => (
                    <li key={item}>
                        <input
                            type="radio"
                            name="theme-dropdown"
                            className="theme-controller btn btn-ghost btn-sm text-base-content justify-start after:-translate-y-[0.15rem]"
                            aria-label={capitalizeFirstLetter(item)}
                            value={item}
                            checked={theme === item}
                            onChange={(e) => {
                                if (e.target.checked) {
                                    setTheme(item);
                                }
                            }}
                        />
                    </li>
                ))}
            </ul>
        </div>
    );
}
