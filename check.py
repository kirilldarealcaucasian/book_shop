# stream = session.stream(stmt, execution_options={"yield_per": 100})
        # async for row in await stream:
        #     cart_item = row._asdict()["CartItem"]  # convert row to dict
        #     print(cart_item)
        #     cart.append(cart_item)