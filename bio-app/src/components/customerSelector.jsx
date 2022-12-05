import { createSignal, createMemo, createEffect, on } from "solid-js";

export default function CustomerSelector(props) {
  const [selectedCustomer, setSelectedCustomer] = createSignal();

  const selectedStateCustomer = createMemo(() => {
    if (props.state?.customers) {
      return selectedCustomer() ?? props.state.customers[0];
    }
  });

  props.setState({ selectedCustomer: selectedStateCustomer });

  createEffect(async () => {
    // safeguard
    const client = props.state?.client;
    if (!client) return;

    // safeguard
    const sc = props.state?.selectedCustomer;
    if (!sc()) return;

    // safeguard
    const movie = props.state?.selectedMovie;
    if (!movie()) return;

    // safeguard
    const seats = props.state?.seats;
    if (!seats) return;

    const response = await client.getAllAsync("orders", {
      customer_id: sc().customer_id,
      event_id: movie().apiId,
    });

    let seatApiIds = [];
    for (let order of response) {
      seatApiIds = seatApiIds.concat(
        order.bookings.map((b) => {
          return b.bookable_item__id;
        })
      );
    }

    // set the seats state to either occupiedBySelectedCustomer if ordered
    for (let seatIndex in seats) {
      let isOccupied = false;
      if (seatApiIds.length > 0) {
        isOccupied = seatApiIds.includes(seats[seatIndex].apiId);
      }
      props.setState(
        "seats",
        [seatIndex],
        "isOccupiedBySelectedUser",
        isOccupied ? true : false
      );
    }
  });

  function changeSelectedCustomer(customer_id) {
    let customer = props.state.customers.find(
      (customer) => customer.customer_id === customer_id
    );
    setSelectedCustomer(customer);
  }

  return (
    <div>
      <label>Kunde</label>
      <select
        id="customerSelector"
        onChange={(e) => changeSelectedCustomer(e.target.value)}
      >
        <For each={props.state.customers}>
          {(customer) => <option>{customer.customer_id}</option>}
        </For>
      </select>
    </div>
  );
}
