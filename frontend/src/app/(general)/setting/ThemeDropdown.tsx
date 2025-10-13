import { BsChevronDown } from 'react-icons/bs';

import { enabledThemes, useTheme } from '@/logic/contexts.ts';
import { capitalizeFirstLetter, cn } from '@/utils.ts';

export function ThemeDropdown() {
    const { theme, setTheme } = useTheme();

    return (
        <div className="dropdown">
            <div tabIndex={0} role="button" className="btn btn-sm bg-base-100 border-base-300 text-base-content">
                {theme}
                <BsChevronDown />
            </div>
            <ul tabIndex={0} className="menu menu-md dropdown-content bg-base-100 rounded-box z-10 w-52 p-2 shadow-2xl">
                {enabledThemes.map((item) => (
                    <li key={item}>
                        <input
                            type="radio"
                            name="theme-dropdown"
                            className={cn(
                                'theme-controller btn btn-ghost btn-sm text-base-content justify-start border-none',
                                theme === item ? 'bg-primary text-primary-content' : '',
                            )}
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
