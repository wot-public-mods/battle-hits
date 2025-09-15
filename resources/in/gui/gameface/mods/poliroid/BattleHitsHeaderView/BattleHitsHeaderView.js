
import { MediaContext } from "../../libs/media.js";
import { ModelObserver } from "../../libs/model.js";
import { playSound } from "../../libs/sound.js";
import { showPopover } from "../../libs/views.js";

const media = MediaContext();

const model = ModelObserver();

const gen_tab = (tabId, tabLabel, isActive) => {

    const wrapper = document.createElement("div");
    wrapper.classList.add("BattleHitsTab");

    wrapper.innerHTML = `
      <div 
        class="
            Tab
            TabBase
            TabBaseThemePrimary
            ${isActive ? "TabBaseActive" : "TabBaseInactive"}
        "
        data-name="Tab"
        data-test-id="${tabId}"
      >
        <div class="TabBackground"></div>
        <div class="TabBackgroundPattern"></div>
        <div class="TabBorder"></div>
        <div class="TabInnerBorderImage"></div>
        <div class="TabContent BattleHitsTabContent">
          <div class="TruncateText">${tabLabel}</div>
        </div>
      </div>
    `;

    // handle events
    wrapper.addEventListener("click", () => {
        playSound("tabs");
        window.model.changeActiveTab({ tabId });
    });

    if (!isActive) {
        wrapper.addEventListener("mouseenter", () => {
            playSound("highlightx");
        });
    }

    return wrapper;
}

const rebuild_tabs = () => {
    const TabsNavigation = document.querySelector('.TabsNavigationContent');
    TabsNavigation.innerHTML = '';
    window.model.menuItems.forEach(item => {
        const tab = gen_tab(item.value.tabId, item.value.tabLabel, item.value.tabId === window.model.activeTab);
        TabsNavigation.appendChild(tab);
    });
};

engine.whenReady.then(() => {

    media.onUpdate(() => {
        rebuild_tabs();
    });
    media.subscribe();

    model.onUpdate(() => {
        rebuild_tabs();
    });
    model.subscribe();

    rebuild_tabs();

    const button = document.querySelector('.SettingsButton');
    button.addEventListener("click", () => {
        model.model.openSettingsPopup();
        playSound("play");
        showPopover(button, "BattleHitsPreferencesPopover");
    });
    button.addEventListener("mouseenter", () => {
        playSound("highlight");
    });
});
