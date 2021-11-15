$("document").ready(function () {
  let render_text = (name, description) => 
    `<div class="d-flex flex-row justify-content-between">
      <div class="me-3 text-muted">${name}</div>
      <div>${description}</div>
    </div>`;
  
  let render_price = (price) => {
    let [i, d] = price.toFixed(2).split('.');
    return `${i}.<small>${d}</small>`;
  }

  let render_discount = discount => `${(discount*100).toFixed(0)}%`;

  let render_tick = (level, is_completed) =>
    `<div class="tick-mark">
      <div class="text-bottom ${is_completed ? 'fw-bold' : ''}">$${level.xp}</div>
      <div class="text-top">
        <div class="
          shadow level-dropdown border mx-auto my-auto 
          ${is_completed ? 'border-warning border-3' : 'border-2'}
          ${is_completed ? 'fw-bold' : ''}">
          ${level.level}
        </div>
        <div class="level-dropdown-info w-100">
          <div class="border rounded shadow-sm bg-white mx-auto p-2">
            ${render_text("Discount free", render_discount(level.discount_free))}
            ${render_text("Discount paid", render_discount(level.discount_paid))}
            ${render_text("Amount", "$"+render_price(level.xp))}
          </div>
        </div>
      </div>
      <div class="tick"></div>
    </div>`;

  $("[data-toggle='cafepass-levels-info']").each(function() {
    let parent = $(this);

    let levels = [];
    parent.find("[data-level]").each(function(i, el) {
      let level_data = $(el);
      levels.push({
        level: Number(level_data.attr("data-level")),
        discount_free: Number(level_data.attr("data-discount-free")),
        discount_paid: Number(level_data.attr("data-discount-paid")),
        xp: Number(level_data.attr("data-xp")),
      });
    });

    levels = levels.sort((L1, L2) => L1.xp > L2.xp);

    let max_xp = levels.reduce((v, o) => Math.max(o.xp, v), 0);
    let min_xp = 0;
    let net_xp = Number(parent.attr("data-value"));
    net_xp = Math.min(max_xp, net_xp);
    let net_progress = net_xp / (max_xp - min_xp);

    // update progress bar
    let progress_bar = parent.find("#level-progress");
    progress_bar.attr("aria-valuemax", max_xp);
    progress_bar.attr("aria-valuemin", min_xp);
    progress_bar.attr("aria-valuenow", net_xp);
    progress_bar.css("width", `${net_progress.toFixed(2)*100}%`)

    // add in tick marks
    let ticks_parent = parent.find("#tick-marks");
    for (let level of levels) {
      let tick_el = $(render_tick(level, net_xp >= level.xp));
      let position =  level.xp / (max_xp - min_xp);
      tick_el.css("left", `${position.toFixed(2)*100}%`);
      ticks_parent.append(tick_el);
    }
  });
});
